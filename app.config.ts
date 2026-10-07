import type { ExpoConfig } from 'expo/config';

/**
 * App identity (decision D8). Change these values here before publishing.
 */
export const APP_IDENTITY = {
  name: 'TOBI Habit',
  slug: 'tobi-habit',
  scheme: 'tobihabit',
  iosBundleIdentifier: 'com.tobihabit.app',
  androidPackage: 'com.tobihabit.app',
  version: '0.1.0',
} as const;

const config: ExpoConfig = {
  name: APP_IDENTITY.name,
  slug: APP_IDENTITY.slug,
  scheme: APP_IDENTITY.scheme,
  version: APP_IDENTITY.version,
  orientation: 'portrait',
  icon: './assets/app/icon.png',
  userInterfaceStyle: 'light',
  ios: {
    bundleIdentifier: APP_IDENTITY.iosBundleIdentifier,
    supportsTablet: false,
  },
  android: {
    package: APP_IDENTITY.androidPackage,
    adaptiveIcon: {
      backgroundColor: '#FFF9F3',
      foregroundImage: './assets/app/android-icon-foreground.png',
      backgroundImage: './assets/app/android-icon-background.png',
      monochromeImage: './assets/app/android-icon-monochrome.png',
    },
    predictiveBackGestureEnabled: false,
  },
  web: {
    favicon: './assets/app/favicon.png',
  },
  plugins: ['expo-router', 'expo-sqlite'],
};

export default config;
