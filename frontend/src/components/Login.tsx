import React from 'react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

interface User {
    user_id: number;
    name: string;
    email: string;
    picture: string;
  }

interface LoginProps {
  onLoginSuccess: (user: User) => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const handleGoogleLoginSuccess = async (credentialResponse: CredentialResponse) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_API}api/google-login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: credentialResponse.credential }),
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const data = await response.json();
      console.log("Collected User Info: ", data);
      localStorage.setItem('token', data.token);
      onLoginSuccess(data.user);
    } catch (error) {
      console.error('Error during Google login:', error);
    }
  };

  return (
    <div>
      <h2>Login to Accomplify</h2>
      <GoogleLogin
        onSuccess={handleGoogleLoginSuccess}
        onError={() => {
          console.log('Login Failed');
        }}
      />
    </div>
  );
};

export default Login;