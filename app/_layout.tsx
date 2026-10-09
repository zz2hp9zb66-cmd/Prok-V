import { type ErrorBoundaryProps, SplashScreen, Stack } from 'expo-router';
import { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { PrimaryButton } from '@/components/PrimaryButton';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { DataProvider } from '@/data/DataProvider';
import { colors, spacing, typography } from '@/theme';

// Keep the native splash until the local database is open, so the cold start
// goes splash → welcome screen without a blank frame in between.
SplashScreen.preventAutoHideAsync();

/** Rendered once the DataProvider is ready (DB opened and migrated). */
function HideNativeSplash() {
  useEffect(() => {
    SplashScreen.hide();
  }, []);
  return null;
}

const detailHeader = (title: string) => ({
  headerShown: true,
  title,
  headerBackTitle: 'Назад',
  headerTintColor: colors.primary,
  headerTitleStyle: { ...typography.h3, color: colors.textPrimary },
  headerStyle: { backgroundColor: colors.background },
  headerShadowVisible: false,
});

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <DataProvider>
        <HideNativeSplash />
        <StatusBar style="dark" />
        <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
          <Stack.Screen name="index" options={{ animation: 'none' }} />
          <Stack.Screen name="onboarding" options={{ gestureEnabled: false }} />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="welcome" />
          <Stack.Screen name="habit/new" options={{ headerShown: false }} />
          <Stack.Screen name="habit/[id]/index" options={detailHeader('Привычка')} />
          <Stack.Screen name="habit/[id]/edit" options={detailHeader('Редактировать привычку')} />
          <Stack.Screen name="reward/new" options={{ headerShown: false }} />
          <Stack.Screen name="reward/[id]/index" options={detailHeader('Награда')} />
          <Stack.Screen name="reward/[id]/edit" options={detailHeader('Редактировать награду')} />
        </Stack>
      </DataProvider>
    </SafeAreaProvider>
  );
}

/** Shown if something unexpected fails (e.g. the local database cannot be opened). */
export function ErrorBoundary({ retry }: ErrorBoundaryProps) {
  useEffect(() => {
    SplashScreen.hide();
  }, []);
  return (
    <View style={styles.error}>
      <AppText variant="h2" align="center">
        Что-то пошло не так
      </AppText>
      <AppText color="textSecondary" align="center">
        Твои данные хранятся на устройстве. Попробуй ещё раз.
      </AppText>
      <PrimaryButton title="Повторить" onPress={retry} />
    </View>
  );
}

const styles = StyleSheet.create({
  error: { flex: 1, justifyContent: 'center', gap: spacing.sm, padding: spacing.md, backgroundColor: colors.background },
});
