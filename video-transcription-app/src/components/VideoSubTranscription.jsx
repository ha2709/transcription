import React, { useEffect, useState } from "react";

const VideoTranscription = () => {
    const [videoFileName, setVideoFileName] = useState("");
    const [srtFileName, setSrtFileName] = useState("");

    useEffect(() => {
        if (videoFileName && srtFileName) {
            const video = document.getElementById("video");
            const subtitlesDiv = document.getElementById("subtitles");

            // Adjust fetch path to match where the SRT files are served from
            fetch(`${process.env.PUBLIC_URL}/text/${srtFileName}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.text();
                })
                .then((srtContent) => {
                    if (!srtContent) {
                        throw new Error("SRT file is empty");
                    }

                    const subtitles = parseSRT(srtContent);

                    video.addEventListener("timeupdate", function () {
                        const currentTime = video.currentTime;
                        const subtitle = getSubtitleForTime(subtitles, currentTime);
                        subtitlesDiv.innerHTML = subtitle ? subtitle.text : "";
                    });
                })
                .catch((error) => console.error("Error loading SRT file:", error));
        }
    }, [videoFileName, srtFileName]);

    function parseSRT(srt) {
        const subtitles = [];
        const lines = srt.split("\n");
        let i = 0;

        while (i < lines.length) {
            const index = parseInt(lines[i], 10);
            const time = lines[i + 1]?.split(" --> ");
            if (!time || time.length !== 2) {
                console.error("Invalid time format in SRT file");
                continue;
            }
            const start = parseTimestamp(time[0]);
            const end = parseTimestamp(time[1]);
            const text = lines.slice(i + 2, i + 4).join(" ");
            subtitles.push({ index, start, end, text });
            i += 4;
        }

        return subtitles;
    }

    function parseTimestamp(timestamp) {
        const [hours, minutes, seconds] = timestamp.split(":");
        const [secs, millis] = seconds.split(",");
        return (
            parseInt(hours, 10) * 3600 +
            parseInt(minutes, 10) * 60 +
            parseInt(secs, 10) +
            parseInt(millis, 10) / 1000
        );
    }

    function getSubtitleForTime(subtitles, time) {
        return subtitles.find(
            (subtitle) => time >= subtitle.start && time <= subtitle.end
        );
    }

    return (
        <div className="container mt-5">
            <h1 className="text-center">Video Transcription</h1>

            <div className="form-group">
                <label htmlFor="videoFileName">Video File Name:</label>
                <input
                    type="text"
                    id="videoFileName"
                    className="form-control"
                    placeholder="Enter video file name (e.g., video.mp4)"
                    value={videoFileName}
                    onChange={(e) => setVideoFileName(e.target.value)}
                />
            </div>
            <div className="form-group mt-3">
                <label htmlFor="srtFileName">SRT File Name:</label>
                <input
                    type="text"
                    id="srtFileName"
                    className="form-control"
                    placeholder="Enter SRT file name (e.g., subtitles.srt)"
                    value={srtFileName}
                    onChange={(e) => setSrtFileName(e.target.value)}
                />
            </div>

            {videoFileName && srtFileName && (
                <div className="video-container mt-4">
                    <video id="video" controls>
                        <source
                            src={`${process.env.PUBLIC_URL}/video/${videoFileName}`}
                            type="video/mp4"
                        />
                        Your browser does not support the video tag.
                    </video>
                    <div id="subtitles" className="subtitles"></div>
                </div>
            )}
        </div>
    );
};

export default VideoTranscription;
