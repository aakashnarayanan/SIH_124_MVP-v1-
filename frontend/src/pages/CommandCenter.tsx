/**
 * CommandCenter — RouteSense Screen 1
 * Matches exact layout from reference mockup:
 *   - 4 Stat Cards at top
 *   - Electric Midnight Map with bus pills & route trail
 *   - 3 Bottom analytics cards (Recent Events, Fleet Summary Donut, Traffic Density Area Chart)
 */

import React, { useState, useEffect } from 'react'
import MapView from '../components/MapView'
import {
  RecentEventsCard,
  TrafficDensityCard,
} from '../components/CommandCenterCards'
import type { Vehicle, DefectMarker, AlertEvent, HealthInfo, H3Cell } from '../types'
import { Bus, Activity, AlertTriangle, Radio } from 'lucide-react'

interface CommandCenterProps {
  vehicles: Vehicle[]
  defects: DefectMarker[]
  alerts: AlertEvent[]
  health: HealthInfo | null
  isConnected: boolean
  isLiveData: boolean
  h3Cells: H3Cell[]
  onClearAlerts?: () => void
}

export default function CommandCenter({
  vehicles,
  defects,
  health,
  isLiveData,
  h3Cells,
}: CommandCenterProps) {
  const [currentTime, setCurrentTime] = useState('')

  useEffect(() => {
    const update = () => {
      const now = new Date()
      setCurrentTime(now.toLocaleTimeString('en-US', { hour12: true }))
    }
    update()
    const timer = setInterval(update, 1000)
    return () => clearInterval(timer)
  }, [])

  const onlineBusCount = vehicles.length
  const activeEventsCount = defects.length
  const roadHazardCount = defects.filter(d => d.confidence >= 0.7).length
  const h3ClusterCount = health?.h3_clusters ?? h3Cells.length

  return (
    <div className="routesense-page command-center-view">
      {/* Top Header */}
      <header className="routesense-page-header">
        <div className="header-left">
          <h2 className="header-main-title">Command Center</h2>
          <p className="header-subtitle">Real-time overview of fleet and urban intelligence</p>
        </div>

        <div className="header-right-meta">
          <div className={`live-status-chip ${isLiveData ? '' : 'presentation'}`}>
            <span className={isLiveData ? 'live-dot-green' : 'live-dot-amber'}></span>
            <span className="live-text">{isLiveData ? 'LIVE' : 'PRESENTATION'}</span>
          </div>
          <div className="live-clock-text">{currentTime || '10:42:18 AM'}</div>
          <div className="header-icon-btn">🔔</div>
          <div className="header-user-avatar">RK</div>
        </div>
      </header>

      {/* 4 RouteSense Stat Cards */}
      <section className="routesense-stats-row">
        <div className="routesense-metric-card">
          <div className="metric-info-col">
            <div className="metric-title">Buses Online</div>
            <div className="metric-value-row">
              <span className="metric-big-num">{onlineBusCount}</span>
            </div>
            <div className="metric-sub-note">{onlineBusCount > 0 ? 'Active telemetry' : 'Awaiting transit node'}</div>
          </div>
          <div className="metric-icon-bubble green">
            <Bus size={22} />
          </div>
        </div>

        <div className="routesense-metric-card">
          <div className="metric-info-col">
            <div className="metric-title">Active Events</div>
            <div className="metric-value-row">
              <span className="metric-big-num">{activeEventsCount}</span>
            </div>
            <div className="metric-sub-note red">Live detections</div>
          </div>
          <div className="metric-icon-bubble red">
            <Activity size={22} />
          </div>
        </div>

        <div className="routesense-metric-card">
          <div className="metric-info-col">
            <div className="metric-title">Road Hazards</div>
            <div className="metric-value-row">
              <span className="metric-big-num">{roadHazardCount}</span>
            </div>
            <div className="metric-sub-note amber">Confidence ≥ 70%</div>
          </div>
          <div className="metric-icon-bubble amber">
            <AlertTriangle size={22} />
          </div>
        </div>

        <div className="routesense-metric-card">
          <div className="metric-info-col">
            <div className="metric-title">High Traffic Zones</div>
            <div className="metric-value-row">
              <span className="metric-big-num">{h3ClusterCount}</span>
            </div>
            <div className="metric-sub-note purple">Uber H3 clusters</div>
          </div>
          <div className="metric-icon-bubble purple">
            <Radio size={22} />
          </div>
        </div>
      </section>

      {/* Central Map Canvas */}
      <section className="routesense-map-section">
        <MapView vehicles={vehicles} defects={defects} h3Cells={h3Cells} showHexOverlay={true} />
      </section>

      {/* Bottom Analytics Cards (2 Balanced Panes) */}
      <section className="command-bottom-cards-row">
        <RecentEventsCard defects={defects} />
        <TrafficDensityCard cells={h3Cells} />
      </section>
    </div>
  )
}
