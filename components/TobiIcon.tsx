import Ionicons from '@expo/vector-icons/Ionicons';
import { Image, StyleSheet, View } from 'react-native';
import { type IconOwner, resolveIcon } from '@/features/icons/iconRegistry';
import { iconColors, radius } from '@/theme';

export interface TobiIconProps {
  /** Stored icon id (null/unknown → the type's default icon). */
  iconId: string | null | undefined;
  owner: IconOwner;
  size?: number;
}

/** Round pastel icon of a habit, goal or wish. Never throws on unknown ids. */
export function TobiIcon({ iconId, owner, size = 44 }: TobiIconProps) {
  const icon = resolveIcon(iconId, owner);
  const color = iconColors[icon.color];
  const glyphSize = Math.round(size * 0.55);
  return (
    <View
      style={[styles.circle, { width: size, height: size, backgroundColor: color.background }]}
      accessibilityLabel={`Иконка: ${icon.label}`}
      testID={`tobi-icon-${icon.id}`}
    >
      {icon.glyph.kind === 'vector' ? (
        <Ionicons name={icon.glyph.name} size={glyphSize} color={color.icon} />
      ) : (
        <Image source={icon.glyph.source} style={{ width: glyphSize, height: glyphSize }} resizeMode="contain" />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  circle: { borderRadius: radius.pill, alignItems: 'center', justifyContent: 'center' },
});
