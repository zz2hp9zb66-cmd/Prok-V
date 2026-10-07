import { Text, type TextProps } from 'react-native';
import { colors, type ColorToken, typography, type TypographyToken } from '@/theme';

export interface AppTextProps extends TextProps {
  variant?: TypographyToken;
  color?: ColorToken;
  align?: 'left' | 'center' | 'right';
}

/** Text bound to Design System typography and color tokens. */
export function AppText({ variant = 'body', color = 'textPrimary', align, style, ...rest }: AppTextProps) {
  return <Text style={[typography[variant], { color: colors[color], textAlign: align }, style]} {...rest} />;
}
