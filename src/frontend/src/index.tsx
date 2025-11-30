import React, { StrictMode, useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { FluentProvider, teamsLightTheme, teamsDarkTheme, Theme, createLightTheme, createDarkTheme, BrandVariants } from "@fluentui/react-components";
import { setEnvData, setApiUrl, config as defaultConfig, toBoolean, getUserInfo, setUserInfoGlobal } from './api/config';
import { UserInfo } from './models';
import { apiService } from './api';

// ALTYCA Brand Colors
const altycaBrand: BrandVariants = {
  10: "#001a14",
  20: "#00331f",
  30: "#004d2b",
  40: "#006638",
  50: "#008047",
  60: "#009955",
  70: "#00b366",
  80: "#00cc77",
  90: "#00e68a",
  100: "#00ff9d",
  110: "#1aff99",
  120: "#33ffaa",
  130: "#4dffbb",
  140: "#66ffcc",
  150: "#80ffdd",
  160: "#99ffee"
};

const altycaLightTheme: Theme = {
  ...createLightTheme(altycaBrand),
};

const altycaDarkTheme: Theme = {
  ...createDarkTheme(altycaBrand),
};

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

const AppWrapper = () => {
  // State to store the current theme
  const [isConfigLoaded, setIsConfigLoaded] = useState(false);
  const [isUserInfoLoaded, setIsUserInfoLoaded] = useState(false);
  // Set default theme to light mode
  const [isDarkMode, setIsDarkMode] = useState(false);
  type ConfigType = typeof defaultConfig;
  const [config, setConfig] = useState<ConfigType>(defaultConfig);
  useEffect(() => {
    const initConfig = async () => {
      window.appConfig = config;
      setEnvData(config);
      setApiUrl(config.API_URL);
      try {
        const response = await fetch('/config');
        let config = defaultConfig;
        if (response.ok) {
          config = await response.json();
          config.ENABLE_AUTH = toBoolean(config.ENABLE_AUTH);
        }

        window.appConfig = config;
        setEnvData(config);
        setApiUrl(config.API_URL);
        setConfig(config);
        let defaultUserInfo = config.ENABLE_AUTH ? await getUserInfo() : ({} as UserInfo);
        window.userInfo = defaultUserInfo;
        setUserInfoGlobal(defaultUserInfo);
        const browserLanguage = await apiService.sendUserBrowserLanguage();
      } catch (error) {
        console.info("frontend config did not load from python", error);
      } finally {
        setIsConfigLoaded(true);
        setIsUserInfoLoaded(true);
      }
    };
    
    initConfig(); // Call the async function inside useEffect
  }, []);
  // Note: Theme is now fixed to light mode (isDarkMode = false)
  // Automatic dark mode detection is disabled
  if (!isConfigLoaded || !isUserInfoLoaded) return <div>Loading...</div>;
  return (
    <StrictMode>
      <FluentProvider theme={isDarkMode ? altycaDarkTheme : altycaLightTheme} style={{ height: "100vh" }}>
        <App />
      </FluentProvider>
    </StrictMode>
  );
};
root.render(<AppWrapper />);
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
