import axios from 'axios';
import React, { useEffect, useState } from 'react';

import GoogleLogin from './GoogleLogin';
import GoogleTranslateLanguageSelector from './GoogleTranslateLanguageSelector';
import LanguageSelector from './LanguageSelector';

const VideoTranscription = () => {
    const [videoUrl, setVideoUrl] = useState('');
    const [language, setLanguage] = useState('en');
    const [taskId, setTaskId] = useState(null);
    const [transcriptionStatus, setTranscriptionStatus] = useState('');
    const [videoFileUrl, setVideoFileUrl] = useState('');
    const [file, setFile] = useState(null); // State for file input
    const [translateLanguage, setTranslateLanguage] = useState('en');
    const [userToken, setUserToken] = useState(null); // Store user token after Google Login

    // Set the base URL for axios requests
    const axiosInstance = axios.create({
        baseURL: 'http://localhost:8000/api', // Replace with your Django server's base URL
    });

    // Handle Google Login success
    const handleGoogleLoginSuccess = (token) => {
        setUserToken(token); // Save the token after successful login
        console.log("Google token saved: ", token);
    };

    // Handle form submission
    const handleSubmit = async (event) => {
        event.preventDefault();
        // if (!userToken) {
        //     alert("Please sign in with Google before submitting the form.");
        //     return;
        // }
        try {
            if (file) {
                await handleSubmitVideoFile(event);
            } else {
                const response = await axiosInstance.post('/transcribe', { videoUrl, language, translateLanguage });
                setTaskId(response.data.task_id);
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

    // Function to handle video file upload submission
    const handleSubmitVideoFile = async (e) => {
        e.preventDefault(); // Prevent the default form submission
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('language', language);
            formData.append('translate_language', translateLanguage);

            try {
                const response = await axiosInstance.post('/upload-video-file', formData, {
                    headers: { 'Content-Type': 'multipart/form-data', 'Authorization': `Bearer ${userToken}` }, // Send token in header
                });

                if (response.status !== 202) {
                    throw new Error('Failed to upload video file');
                }

                setTaskId(response.data.task_id);
                setTranscriptionStatus('File uploaded successfully. Transcription in progress...');
            } catch (error) {
                console.error('Error uploading video file:', error);
                setTranscriptionStatus('Failed to upload video file. Please try again.');
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

            {/* Add Google Login Component */}
            <div className="mb-3">
                <GoogleLogin onLoginSuccess={handleGoogleLoginSuccess} />
            </div>

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
