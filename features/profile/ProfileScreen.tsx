import Constants from 'expo-constants';
import { router } from 'expo-router';
import { StyleSheet, Switch, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { Card } from '@/components/Card';
import { Icon, type IconName } from '@/components/Icon';
import { Screen } from '@/components/Screen';
import { SecondaryButton } from '@/components/SecondaryButton';
import { colors, spacing } from '@/theme';

function SettingRow({ icon, title, hint }: { icon: IconName; title: string; hint: string }) {
  return (
    <View style={styles.row}>
      <Icon name={icon} color="textSecondary" />
      <View style={styles.text}>
        <AppText variant="bodyStrong">{title}</AppText>
        <AppText variant="caption" color="textSecondary">
          {hint}
        </AppText>
      </View>
      <Switch
        value={false}
        disabled
        accessibilityLabel={`${title}: недоступно`}
        trackColor={{ false: colors.border, true: colors.primary }}
      />
    </View>
  );
}

/**
 * «Профиль» (§18, D5): settings, not an account. Sound and haptics are
 * placeholders until sound design / the test build.
 */
export function ProfileScreen() {
  const version = Constants.expoConfig?.version ?? '—';
  return (
    <Screen>
      <AppText variant="h1">Профиль</AppText>

      <AppText variant="h3">Настройки</AppText>
      <Card>
        <SettingRow icon="volume-high-outline" title="Звук" hint="Появится позже" />
        <SettingRow icon="phone-portrait-outline" title="Тактильная отдача" hint="Появится позже" />
      </Card>

      <AppText variant="h3">О приложении</AppText>
      <Card>
        <AppText>
          TOBI Habit помогает выполнять привычки, копить баллы и обменивать их на заранее выбранные цели и желания.
          TOBI награждает действие и никогда не ругает за пропуски.
        </AppText>
        <View style={styles.row}>
          <AppText color="textSecondary" style={styles.text}>
            Версия
          </AppText>
          <AppText variant="bodyStrong">{version}</AppText>
        </View>
      </Card>
      <SecondaryButton title="Посмотреть приветствие" onPress={() => router.push('/welcome')} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, minHeight: 44 },
  text: { flex: 1 },
});
