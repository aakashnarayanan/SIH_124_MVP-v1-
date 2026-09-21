/**
 * Pre-configured route waypoints and transit schedule for RouteSense
 */

// Circular route — Connaught Place ring (matches route_1.csv, 2 laps, 50pts/lap)
// Center: 28.6315, 77.2167  |  r≈890m
export const ROUTE_17_WAYPOINTS: [number, number][] = [
  [28.6315, 77.2247], // 0°
  [28.6372, 77.2224], // 36°
  [28.6395, 77.2167], // 72°
  [28.6372, 77.2110], // 108°
  [28.6315, 77.2087], // 144°
  [28.6258, 77.2110], // 180°
  [28.6235, 77.2167], // 216°
  [28.6258, 77.2224], // 252°
  [28.6315, 77.2247], // 360° — closes the loop
]


export const ROUTE_17_STOPS = [
  { name: 'Central Station', time: '09:30 AM', passed: true },
  { name: 'City Hospital', time: '10:15 AM', passed: true },
  { name: 'Main Market', time: '10:50 AM', current: true },
  { name: 'Tech Park', time: '11:05 AM', passed: false },
  { name: 'Railway Station', time: '11:20 AM', passed: false },
]

export const FLEET_DETAILS_MOCK: Record<string, { route: string; speed: number; eta: number; dist: string; next: string; pass: string }> = {
  bus_1: { route: 'Route 17: Central → Railway Station', speed: 28, eta: 8, dist: '32.4 km', next: 'Main Market 0.8 km', pass: '24/40' },
  bus_2: { route: 'Route 04: South Ext → Connaught Place', speed: 34, eta: 14, dist: '18.2 km', next: 'Defense Colony 1.2 km', pass: '31/40' },
  bus_3: { route: 'Route 22: Rohini → Kashmiri Gate', speed: 22, eta: 6, dist: '24.8 km', next: 'Pitampura 0.5 km', pass: '38/40' },
  bus_4: { route: 'Route 11: Dwarka → Airport T3', speed: 45, eta: 18, dist: '15.6 km', next: 'Aero City 2.1 km', pass: '19/40' },
  bus_5: { route: 'Route 09: Noida Sec 18 → ITO', speed: 0, eta: 0, dist: '29.0 km', next: 'Depot (Offline)', pass: '0/40' },
}
