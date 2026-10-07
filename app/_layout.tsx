import { type ErrorBoundaryProps, Stack } from 'expo-router';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { PrimaryButton } from '@/components/PrimaryButton';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { DataProvider } from '@/data/DataProvider';
import { colors, spacing, typography } from '@/theme';

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
        <StatusBar style="dark" />
        <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="onboarding" options={{ gestureEnabled: false }} />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="habit/new" options={detailHeader('Новая привычка')} />
          <Stack.Screen name="habit/[id]/index" options={detailHeader('Привычка')} />
          <Stack.Screen name="habit/[id]/edit" options={detailHeader('Редактировать привычку')} />
          <Stack.Screen name="reward/new" options={detailHeader('Новая награда')} />
          <Stack.Screen name="reward/[id]/index" options={detailHeader('Награда')} />
          <Stack.Screen name="reward/[id]/edit" options={detailHeader('Редактировать награду')} />
        </Stack>
      </DataProvider>
    </SafeAreaProvider>
  );
}

/** Shown if something unexpected fails (e.g. the local database cannot be opened). */
export function ErrorBoundary({ retry }: ErrorBoundaryProps) {
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
