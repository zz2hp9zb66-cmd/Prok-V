import { Image, StyleSheet, View } from 'react-native';
import type { TobiState } from '@/features/tobi/states';
import { tobiImages } from '@/features/tobi/tobiAssets';
import { colors, componentRadius, spacing } from '@/theme';
import { AppText } from './AppText';

export interface TOBIHeroProps {
  state: TobiState;
  size?: number;
}

/**
 * TOBI Zone. Shows the pre-rendered asset for `state`; until assets are
 * provided it renders a neutral placeholder (TOBI is never drawn in code).
 */
export function TOBIHero({ state, size = 160 }: TOBIHeroProps) {
  const source = tobiImages[state];
  if (source) {
    return <Image source={source} style={{ width: size, height: size }} resizeMode="contain" accessibilityLabel="TOBI" />;
  }
  return (
    <View style={[styles.placeholder, { width: size, height: size }]} accessibilityLabel="TOBI">
      <AppText variant="small" color="textSecondary" align="center" numberOfLines={2}>
        {state}
      </AppText>
    </View>
  );
}

const styles = StyleSheet.create({
  placeholder: {
    alignSelf: 'center',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xs,
    borderRadius: componentRadius.panel,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
});
