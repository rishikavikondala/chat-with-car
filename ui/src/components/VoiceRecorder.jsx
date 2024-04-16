import React, { useState, useRef } from 'react';
import axios from 'axios';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
`;

const Button = styled.button`
  padding: 10px 20px;
  margin: 10px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #0056b3;
  }

  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
`;

const TranscribedTextContainer = styled.div`
  margin-top: 20px;
  text-align: center;
`;

const ResponseHeader = styled.h3`
  font-family: Arial, sans-serif;
`;

const TranscribedText = styled.p`
  font-family: Arial, sans-serif;
`;

const VoiceRecorder = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcribedText, setTranscribedText] = useState('');
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const streamRef = useRef(null);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;

            chunksRef.current = [];

            mediaRecorder.addEventListener('dataavailable', (event) => {
                chunksRef.current.push(event.data);
            });

            mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
                sendAudioToAPI(audioBlob);
            });

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error('Error starting recording:', error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();

            if (streamRef.current) {
                streamRef.current.getTracks().forEach((track) => track.stop());
                streamRef.current = null;
            }

            setIsRecording(false);
        }
    };

    const sendAudioToAPI = async (audioBlob) => {
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');

            const response = await axios.post('http://localhost:8000/transcribe', formData);
            setTranscribedText(response.data.text);
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 500) {
                setTranscribedText('Error: Invalid command. Please try again.');
            } else {
                console.error('Error sending audio to API:', error);
                setTranscribedText('Error: Failed to transcribe audio. Please try again.');
            }
        }
    };

    return (
        <Container>
            <div>
                <Button onClick={startRecording} disabled={isRecording}>
                    Start Recording
                </Button>
                <Button onClick={stopRecording} disabled={!isRecording}>
                    Stop Recording
                </Button>
            </div>
            {transcribedText && (
                <TranscribedTextContainer>
                    <ResponseHeader>Response from Claude:</ResponseHeader>
                    <TranscribedText>{transcribedText}</TranscribedText>
                </TranscribedTextContainer>
            )}
        </Container>
    );
};

export default VoiceRecorder;