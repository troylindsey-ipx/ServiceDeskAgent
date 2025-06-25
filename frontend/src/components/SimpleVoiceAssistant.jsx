import {
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
  useTrackTranscription,
  useLocalParticipant,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";
import "./SimpleVoiceAssistant.css";

const Message = ({ type, text }) => {
  return <div className="message">
    <strong className={`message-${type}`}>
      {type === "agent" ? "Agent: " : "You: "}
    </strong>
    <span className="message-text">{text}</span>
  </div>;
};

Message.propTypes = {
  type: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
};

const SimpleVoiceAssistant = () => {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const localParticipant = useLocalParticipant();
  const { segments: userTranscriptions } = useTrackTranscription({
    publication: localParticipant.microphoneTrack,
    source: Track.Source.Microphone,
    participant: localParticipant.localParticipant,
  });

  const [messages, setMessages] = useState([]);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const conversationRef = useRef(null);
  const scrollTimeoutRef = useRef(null);

  useEffect(() => {
    const allMessages = [
      ...(agentTranscriptions?.map((t) => ({ ...t, type: "agent" })) ?? []),
      ...(userTranscriptions?.map((t) => ({ ...t, type: "user" })) ?? []),
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
    setMessages(allMessages);
  }, [agentTranscriptions, userTranscriptions]);

  // Auto-scroll to bottom when new messages arrive, unless user is scrolling
  useEffect(() => {
    if (!isUserScrolling && conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
  }, [messages, isUserScrolling]);

  // Handle scroll events to detect if user is manually scrolling
  const handleScroll = () => {
    if (!conversationRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = conversationRef.current;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10; // 10px tolerance
    
    if (!isAtBottom) {
      setIsUserScrolling(true);
      
      // Clear existing timeout
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      // Resume auto-scrolling after 3 seconds of no scrolling
      scrollTimeoutRef.current = setTimeout(() => {
        setIsUserScrolling(false);
      }, 3000);
    } else {
      setIsUserScrolling(false);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    }
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="voice-assistant-container">
      <div className="visualizer-container">
        <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
      </div>
      <div className="control-section">
        <VoiceAssistantControlBar />
        <div 
          className="conversation" 
          ref={conversationRef}
          onScroll={handleScroll}
        >
          {messages.map((msg, index) => (
            <Message key={msg.id || index} type={msg.type} text={msg.text} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default SimpleVoiceAssistant;
