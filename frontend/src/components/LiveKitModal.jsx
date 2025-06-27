import { useState, useCallback } from "react";
import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import PropTypes from "prop-types";
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

const LiveKitModal = ({ setShowSupport }) => {
  const [isSubmittingName, setIsSubmittingName] = useState(true);
  const [name, setName] = useState("");
  const [token, setToken] = useState(null);

  const getToken = useCallback(async (userName) => {
    try {
      console.log("run")
      const response = await fetch(
        `/api/getToken?name=${encodeURIComponent(userName)}`
      );
      const token = await response.text();
      setToken(token);
      setIsSubmittingName(false);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      getToken(name);
    }
  };

  const handleDisconnect = useCallback(async () => {
    try {
      // Request token usage summary before closing
      console.log("Session ended - requesting token usage summary");
      // Note: The backend services will handle token tracking cleanup automatically
      // when the LiveKit room connection is closed
    } catch (error) {
      console.error("Error handling disconnect:", error);
    } finally {
      // Reset all state to allow for clean reconnection
      setToken(null);
      setName("");
      setIsSubmittingName(true);
      setShowSupport(false);
    }
  }, [setShowSupport]);

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="support-room">
          {isSubmittingName ? (
            <form onSubmit={handleNameSubmit} className="name-form">
              <h2>Enter your name to connect with support</h2>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
              <button type="submit">Connect</button>
              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowSupport(false)}
              >
                Cancel
              </button>
            </form>
          ) : token ? (
            <LiveKitRoom
              serverUrl={import.meta.env.VITE_LIVEKIT_URL}
              token={token}
              connect={true}
              video={false}
              audio={true}
              onDisconnected={handleDisconnect}
            >
              <RoomAudioRenderer />
              <SimpleVoiceAssistant />
            </LiveKitRoom>
          ) : null}
        </div>
      </div>
    </div>
  );
};

LiveKitModal.propTypes = {
  setShowSupport: PropTypes.func.isRequired,
};

export default LiveKitModal;
