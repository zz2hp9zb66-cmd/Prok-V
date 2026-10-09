import { StyleSheet, View } from 'react-native';
import { spacing } from '@/theme';
import { AppText } from './AppText';

/** Centered title (+ optional text) at the top of a room screen panel. */
export function PanelHeading({ title, text }: { title: string; text?: string }) {
  return (
    <View style={styles.heading}>
      <AppText variant="h1" align="center" accessibilityRole="header">
        {title}
      </AppText>
      {text ? (
        <AppText color="textSecondary" align="center">
          {text}
        </AppText>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  heading: { gap: spacing.xs },
});
