import { StyleSheet } from 'react-native';
import { AppText } from './AppText';
import { Card } from './Card';

export interface StatisticCardProps {
  label: string;
  value: string | number;
}

export function StatisticCard({ label, value }: StatisticCardProps) {
  return (
    <Card style={styles.card}>
      <AppText variant="h2">{value}</AppText>
      <AppText variant="caption" color="textSecondary">
        {label}
      </AppText>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { flex: 1, minWidth: '45%' },
});
