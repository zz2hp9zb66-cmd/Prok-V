import { Tabs } from 'expo-router';
import { BottomNavigation, type BottomNavigationItem } from '@/components/BottomNavigation';

/** Bottom navigation (§6): Задачи · Награды · Статистика · Профиль. */
const TABS: BottomNavigationItem[] = [
  { name: 'tasks', title: 'Задачи', icon: 'checkmark-circle-outline' },
  { name: 'rewards', title: 'Награды', icon: 'gift-outline' },
  { name: 'statistics', title: 'Статистика', icon: 'stats-chart-outline' },
  { name: 'profile', title: 'Профиль', icon: 'settings-outline' },
];

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false }} tabBar={(props) => <BottomNavigation {...props} items={TABS} />}>
      {TABS.map((tab) => (
        <Tabs.Screen key={tab.name} name={tab.name} options={{ title: tab.title }} />
      ))}
    </Tabs>
  );
}
