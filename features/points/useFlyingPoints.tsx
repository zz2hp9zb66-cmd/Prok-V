import { useCallback, useRef, useState } from 'react';
import { StyleSheet, View, type GestureResponderEvent } from 'react-native';
import { FlyingPoints, type Point } from './FlyingPoints';

interface Flight {
  id: number;
  amount: number;
  /** Null until positions are measured. */
  path: { from: Point; to: Point } | null;
}

/**
 * Coordinates the «+N → counter» animation. `pendingAmount` is the sum still
 * in flight, so the counter shows the old value until the points land.
 */
export function useFlyingPoints() {
  const overlayRef = useRef<View>(null);
  const targetRef = useRef<View>(null);
  const [flights, setFlights] = useState<Flight[]>([]);
  const nextId = useRef(0);

  const finish = useCallback((id: number) => setFlights((all) => all.filter((f) => f.id !== id)), []);

  const launch = useCallback((amount: number, event?: GestureResponderEvent) => {
    const overlay = overlayRef.current;
    const target = targetRef.current;
    if (!overlay || !target) return;
    // Register synchronously so the counter keeps the old value until landing.
    const id = ++nextId.current;
    setFlights((all) => [...all, { id, amount, path: null }]);
    // Safety net: the counter must never stay behind if an animation is lost.
    setTimeout(() => finish(id), 3000);
    const tapX = event?.nativeEvent.pageX ?? 0;
    const tapY = event?.nativeEvent.pageY ?? 0;
    overlay.measureInWindow((ox, oy) => {
      target.measureInWindow((tx, ty, tw, th) => {
        const path = {
          from: { x: tapX - ox - 40, y: tapY - oy - 20 },
          to: { x: tx - ox + tw / 2 - 20, y: ty - oy + th / 2 - 16 },
        };
        setFlights((all) => all.map((f) => (f.id === id ? { ...f, path } : f)));
      });
    });
  }, [finish]);

  const overlay = (
    <View ref={overlayRef} style={StyleSheet.absoluteFill} pointerEvents="none" collapsable={false}>
      {flights.map((f) =>
        f.path ? (
          <FlyingPoints key={f.id} amount={f.amount} from={f.path.from} to={f.path.to} onDone={() => finish(f.id)} />
        ) : null,
      )}
    </View>
  );

  const pendingAmount = flights.reduce((sum, f) => sum + f.amount, 0);
  return { overlay, targetRef, launch, pendingAmount };
}
