import { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet } from 'react-native';
import { AppText } from '@/components/AppText';
import { spacing } from '@/theme';

export interface Point {
  x: number;
  y: number;
}

export interface FlyingPointsProps {
  amount: number;
  from: Point;
  to: Point;
  onDone: () => void;
}

/**
 * «+10» that pops up at the tap point and flies into the balance counter
 * (§19). Purely visual; the points are already saved when this runs.
 */
export function FlyingPoints({ amount, from, to, onDone }: FlyingPointsProps) {
  const pop = useRef(new Animated.Value(0)).current;
  const fly = useRef(new Animated.Value(0)).current;
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  useEffect(() => {
    const animation = Animated.sequence([
      Animated.spring(pop, { toValue: 1, useNativeDriver: true, friction: 5 }),
      Animated.delay(250),
      Animated.timing(fly, { toValue: 1, duration: 650, easing: Easing.in(Easing.cubic), useNativeDriver: true }),
    ]);
    animation.start(() => onDoneRef.current());
    return () => animation.stop();
  }, [pop, fly]);

  const translateX = fly.interpolate({ inputRange: [0, 1], outputRange: [from.x, to.x] });
  const translateY = Animated.add(
    fly.interpolate({ inputRange: [0, 1], outputRange: [from.y, to.y] }),
    pop.interpolate({ inputRange: [0, 1], outputRange: [0, -spacing.md] }),
  );
  const scale = Animated.multiply(pop, fly.interpolate({ inputRange: [0, 1], outputRange: [1, 0.6] }));
  const opacity = fly.interpolate({ inputRange: [0, 0.85, 1], outputRange: [1, 1, 0] });

  return (
    <Animated.View
      style={[styles.container, { opacity, transform: [{ translateX }, { translateY }, { scale }] }]}
    >
      <AppText variant="h2" color="primary">
        +{amount}
      </AppText>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: { position: 'absolute', left: 0, top: 0, pointerEvents: 'none' },
});
