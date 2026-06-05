import { useEffect } from 'react';
import { useAppState } from '../../store/AppContext';

const NOTIFICATION_TIMEOUT_MS = 3500;

export function NotificationCenter() {
  const { state, dispatch } = useAppState();

  useEffect(() => {
    if (state.notifications.length === 0) {
      return;
    }

    const timers = state.notifications.map((notification) =>
      window.setTimeout(() => {
        dispatch({
          type: 'REMOVE_NOTIFICATION',
          payload: {
            notificationId: notification.id
          }
        });
      }, NOTIFICATION_TIMEOUT_MS)
    );

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, [dispatch, state.notifications]);

  if (state.notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-center" aria-live="polite">
      {state.notifications.map((notification) => (
        <article
          key={notification.id}
          className={`notification-card ${notification.type}`}
        >
          <div>
            <strong>{notification.title}</strong>
            {notification.message && <span>{notification.message}</span>}
          </div>

          <button
            type="button"
            aria-label="Close notification"
            onClick={() =>
              dispatch({
                type: 'REMOVE_NOTIFICATION',
                payload: {
                  notificationId: notification.id
                }
              })
            }
          >
            ×
          </button>
        </article>
      ))}
    </div>
  );
}