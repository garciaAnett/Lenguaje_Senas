import { useEffect, useState } from 'react';
import { checkHealth } from '../api/mockApi';

export default function HealthStatus() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    checkHealth().then(setStatus);
  }, []);

  if (!status) return null;

  const isMock = status.status === 'mock';
  return (
    <div className={`health-badge ${isMock ? 'mock' : 'live'}`}>
      {isMock ? '⚠ Backend mock' : '✓ Backend conectado'}
    </div>
  );
}
