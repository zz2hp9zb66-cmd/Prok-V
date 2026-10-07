import type { BottomTabBarProps } from 'expo-router/tabs';
import { Pressable, StyleSheet, View } from 'react-native';
import { colors, spacing } from '@/theme';
import { AppText } from './AppText';
import { Icon, type IconName } from './Icon';

export interface BottomNavigationItem {
  name: string;
  title: string;
  icon: IconName;
}

/** Bottom navigation (§6) rendered as the tab bar of the Tabs navigator. */
export function BottomNavigation({ state, navigation, insets, items }: BottomTabBarProps & { items: BottomNavigationItem[] }) {
  return (
    <View style={[styles.bar, { paddingBottom: Math.max(insets.bottom, spacing.xs) }]}>
      {state.routes.map((route, index) => {
        const item = items.find((i) => i.name === route.name);
        if (!item) return null;
        const focused = state.index === index;
        const onPress = () => {
          const event = navigation.emit({ type: 'tabPress', target: route.key, canPreventDefault: true });
          if (!focused && !event.defaultPrevented) navigation.navigate(route.name, route.params);
        };
        return (
          <Pressable
            key={route.key}
            accessibilityRole="tab"
            accessibilityState={{ selected: focused }}
            accessibilityLabel={item.title}
            onPress={onPress}
            style={styles.item}
          >
            <Icon name={item.icon} color={focused ? 'primary' : 'textSecondary'} />
            <AppText variant="small" color={focused ? 'primary' : 'textSecondary'}>
              {item.title}
            </AppText>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    paddingTop: spacing.xs,
  },
  item: { flex: 1, alignItems: 'center', gap: 2, minHeight: 44, justifyContent: 'center' },
});
