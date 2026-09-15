export function startHeartbeat(send: () => void, timeout: () => void) {
	let lastActivity = performance.now();
	const timer = setInterval(() => {
		const idleMs = performance.now() - lastActivity;
		if (idleMs >= 3000) {
			clearInterval(timer);
			timeout();
		} else if (idleMs >= 1000) {
			send();
		}
	}, 1000);
	return {
		received: () => {
			lastActivity = performance.now();
		},
		stop: () => clearInterval(timer)
	};
}
