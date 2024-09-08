import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Home from './components/Home';

const App = () => {
  const clientId = "898311655508-i1jgcqald2be9erruua7mlo65nse22kg.apps.googleusercontent.com";
  console.log("CLIENT ID: ", clientId);
  return (
    <GoogleOAuthProvider clientId={clientId || ''}>
      <Home />
    </GoogleOAuthProvider>
  );
};

export default App;