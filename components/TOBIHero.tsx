import { Image, StyleSheet, View } from 'react-native';
import type { TobiState } from '@/features/tobi/states';
import { tobiRenders } from '@/features/tobi/tobiAssets';
import { colors, componentRadius, spacing } from '@/theme';
import { AppText } from './AppText';

export interface TOBIHeroProps {
  state: TobiState;
  /** Square box side. `width`/`height` override it for non-square renders. */
  size?: number;
  width?: number;
  height?: number;
}

/**
 * TOBI Zone. Shows the pre-rendered asset for `state`; until assets are
 * provided it renders a neutral placeholder (TOBI is never drawn in code).
 */
export function TOBIHero({ state, size = 160, width = size, height = size }: TOBIHeroProps) {
  const source = tobiRenders[state]?.source;
  if (source) {
    return <Image source={source} style={{ width, height }} resizeMode="contain" accessibilityLabel="TOBI" />;
  }
  return (
    <View style={[styles.placeholder, { width, height }]} accessibilityLabel="TOBI">
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
