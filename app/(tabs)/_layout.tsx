import Ionicons from '@expo/vector-icons/Ionicons';
import { Tabs } from 'expo-router';
import type { ComponentProps } from 'react';
import { colors, sizes } from '@/theme';

type IconName = ComponentProps<typeof Ionicons>['name'];

/** Bottom navigation (§6): Задачи · Награды · Статистика · Профиль. */
const TABS: { name: string; title: string; icon: IconName }[] = [
  { name: 'tasks', title: 'Задачи', icon: 'checkmark-circle-outline' },
  { name: 'rewards', title: 'Награды', icon: 'gift-outline' },
  { name: 'statistics', title: 'Статистика', icon: 'stats-chart-outline' },
  { name: 'profile', title: 'Профиль', icon: 'settings-outline' },
];

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
      }}
    >
      {TABS.map((tab) => (
        <Tabs.Screen
          key={tab.name}
          name={tab.name}
          options={{
            title: tab.title,
            tabBarIcon: ({ color }) => <Ionicons name={tab.icon} size={sizes.iconMd} color={color} />,
          }}
        />
      ))}
    </Tabs>
  );
}
