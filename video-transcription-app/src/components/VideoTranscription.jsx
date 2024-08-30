import axios from 'axios';
import React, { useEffect, useState } from 'react';

import GoogleTranslateLanguageSelector from './GoogleTranslateLanguageSelector'; // Adjust the path if necessary
import LanguageSelector from './LanguageSelector'; // Adjust the import path as needed

const VideoTranscription = () => {
    const [videoUrl, setVideoUrl] = useState('');
    const [language, setLanguage] = useState('en');
    const [taskId, setTaskId] = useState(null);
    const [transcriptionStatus, setTranscriptionStatus] = useState('');
    const [videoFileUrl, setVideoFileUrl] = useState('');
    const [file, setFile] = useState(null); // State for file input
    const [translateLanguage, setTranslateLanguage] = useState('en');

    // Set the base URL for axios requests
    const axiosInstance = axios.create({
        baseURL: 'http://localhost:8000/api', // Replace with your Django server's base URL
    });

    // Handle form submission
    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            // Call different submission logic depending on whether a file is uploaded
            if (file) {
                await handleSubmitFile(event);
            } else {
                // Assuming you want to handle URL submission separately
                const response = await axiosInstance.post('/transcribe', { videoUrl, language, translateLanguage });
                setTaskId(response.data.task_id);
                // setTaskId("4f00b060-e2b9-4045-b65f-778a3fe7e96f")
                setTranscriptionStatus('Processing...');
            }
        } catch (error) {
            console.error('Error starting transcription:', error);
        }
    };

    // Function to handle file change and prepare for upload
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
    };

    // Function to handle file upload submission
    const handleSubmitFile = async (e) => {
        e.preventDefault(); // Prevent the default form submission
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('language', language);
            formData.append('translate_language', translateLanguage);

            try {
                const response = await fetch('http://localhost:8000/api/upload-video-file/', {  // Corrected the endpoint URL
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error('Failed to upload file');
                }

                const data = await response.json();
                setTaskId(data.task_id);
                // setTaskId("4f00b060-e2b9-4045-b65f-778a3fe7e96f")
                setTranscriptionStatus('File uploaded successfully. Transcription in progress...');
            } catch (error) {
                console.error('Error uploading file:', error);
                setTranscriptionStatus('Failed to upload file. Please try again.');
            }
        }
    };

    // Poll the backend for task status
    useEffect(() => {
        if (taskId) {
            const interval = setInterval(async () => {
                try {
                    const statusResponse = await axiosInstance.get(`/task-status/${taskId}`);
                    if (statusResponse.data.status === 'completed') {
                        setTranscriptionStatus('Completed');
                        setVideoFileUrl(`http://localhost:8000/media/out/output-${taskId}.mp4`);
                        clearInterval(interval);
                    } else if (statusResponse.data.status === 'failed') {
                        setTranscriptionStatus('Failed');
                        clearInterval(interval);
                    } else {
                        setTranscriptionStatus(statusResponse.data.status);
                    }
                } catch (error) {
                    console.error('Error fetching task status:', error);
                }
            }, 5000); // Poll every 5 seconds
            return () => clearInterval(interval);
        }
    }, [taskId]);

    return (
        <div className="container mt-5">
            <h1 className="text-center">Video Transcription</h1>
            <form onSubmit={handleSubmit} className="mt-4">
                <div className="form-group">
                    <label htmlFor="videoUrl">Video URL:</label>
                    <input
                        type="text"
                        id="videoUrl"
                        className="form-control"
                        placeholder="Enter video URL"
                        value={videoUrl}
                        onChange={(e) => setVideoUrl(e.target.value)}
                    />
                </div>
                <div className="form-group mt-3">
                    <label htmlFor="fileInput">Or Upload Video File:</label>
                    <input
                        type="file"
                        id="fileInput"
                        className="form-control"
                        onChange={handleFileChange}
                    />
                </div>
                <div className="form-group mt-3">
                    <LanguageSelector language={language} setLanguage={setLanguage} />
                </div>
                <div>
                    <h1>Translate Language Selector</h1>
                    <GoogleTranslateLanguageSelector
                        translateLanguage={translateLanguage}
                        setTranslateLanguage={setTranslateLanguage}
                    />
                </div>
                <button type="submit" className="btn btn-primary mt-4">
                    Start Transcription
                </button>
            </form>

            {taskId && <p className="mt-3">Task ID: {taskId}</p>}
            {transcriptionStatus && <p className="mt-3">Status: {transcriptionStatus}</p>}

            {videoFileUrl && (
                <div className="mt-4">
                    <h2>Transcription Completed</h2>
                    <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden' }}>
                        <video controls style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                            <source src={videoFileUrl} type="video/mp4" />
                            <track kind="subtitles" srcLang={language} src={videoFileUrl.replace('.mp4', '.srt')} default />
                            Your browser does not support the video tag.
                        </video>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoTranscription;
