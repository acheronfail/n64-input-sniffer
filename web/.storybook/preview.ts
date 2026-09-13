import type { Preview } from '@storybook/sveltekit';
import '../src/routes/layout.css';
const preview: Preview = {
	parameters: {
		layout: 'fullscreen',
		backgrounds: { default: 'dark' },
		viewport: {
			options: {
				obs: { name: 'OBS narrow sidebar', styles: { width: '280px', height: '1080px' } },
				phone: { name: 'Phone', styles: { width: '390px', height: '844px' } },
				desktop: { name: 'Desktop', styles: { width: '1440px', height: '900px' } }
			}
		}
	}
};
export default preview;
