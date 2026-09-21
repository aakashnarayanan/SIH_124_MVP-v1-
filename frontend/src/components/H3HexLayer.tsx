/**
 * H3HexLayer — renders H3 hexagonal density cells as Leaflet Polygon overlays
 * Renders server-authoritative H3 boundaries so map and backend metrics agree.
 * Coloring is based on the combined intensity of traffic observations AND defect reports
 * so hexes appear even when buses report only potholes (no traffic_density detections).
 */

import { Polygon, Tooltip } from 'react-leaflet'
import type { LatLngExpression } from 'leaflet'
import type { H3Cell } from '../types'

interface H3HexLayerProps {
  cells: H3Cell[]
}

function getHexColor(score: number): { color: string; fill: string; opacity: number } {
  if (score >= 5) return { color: '#ef4444', fill: '#ef4444', opacity: 0.55 }
  if (score >= 3) return { color: '#f97316', fill: '#f97316', opacity: 0.45 }
  if (score >= 2) return { color: '#f59e0b', fill: '#f59e0b', opacity: 0.38 }
  if (score >= 1) return { color: '#06b6d4', fill: '#06b6d4', opacity: 0.28 }
  return { color: '#10b981', fill: '#10b981', opacity: 0.20 }
}

function H3HexLayer({ cells }: H3HexLayerProps) {
  if (cells.length === 0) return null

  return (
    <>
      {cells.map(cell => {
        try {
          const traffic = cell.traffic_count ?? cell.count ?? 0
          const defects = cell.unique_defects ?? cell.defect_reports ?? 0
          // Use max of traffic and defects so pothole-only buses still light up hexes
          const score = Math.max(traffic, defects, cell.count ?? 0)
          const positions: LatLngExpression[] = cell.coordinates.map(([lat, lng]) => [lat, lng])
          const { color, fill, opacity } = getHexColor(score)

          return (
            <Polygon
              key={cell.h3_index}
              positions={positions}
              pathOptions={{
                color,
                fillColor: fill,
                fillOpacity: opacity,
                weight: 1.5,
                opacity: 0.85,
              }}
            >
              <Tooltip sticky>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12 }}>
                  <div><strong>{traffic}</strong> traffic observations</div>
                  <div><strong>{defects}</strong> unique defect{defects !== 1 ? 's' : ''}</div>
                  <div style={{ color: '#94a3b8', fontSize: 10, marginTop: 2 }}>
                    H3: {cell.h3_index.slice(0, 12)}…
                  </div>
                </div>
              </Tooltip>
            </Polygon>
          )
        } catch {
          return null
        }
      })}
    </>
  )
}

export default H3HexLayer

