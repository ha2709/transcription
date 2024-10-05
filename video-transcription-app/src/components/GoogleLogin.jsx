import { useEffect } from "react";

const GoogleLogin = () => {
  useEffect(() => {
    window.google.accounts.id.initialize({
      client_id: "YOUR_GOOGLE_CLIENT_ID",
      callback: handleCallbackResponse,
    });
    window.google.accounts.id.renderButton(
      document.getElementById("signInDiv"),
      { theme: "outline", size: "large" } // Customize button options
    );
  }, []);

  const handleCallbackResponse = (response) => {
    console.log("Encoded JWT ID token: " + response.credential);
    // Send this JWT token to your FastAPI backend for verification
    fetch("http://localhost:8000/auth/google", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token: response.credential }),
    })
      .then((response) => response.json())
      .then((data) => console.log("Server response", data));
  };

  return (
    <div>
      <div id="signInDiv"></div>
    </div>
  );
};

export default GoogleLogin;
