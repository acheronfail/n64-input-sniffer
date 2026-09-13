import type { Meta, StoryObj } from '@storybook/sveltekit';
import { expect, userEvent, within } from 'storybook/test';
import ControllerDashboard from './ControllerDashboard.svelte';
import { decodeFrame, emptyState } from '../controller';

const controllers = [
	decodeFrame(new Uint8Array([0, 0x80, 0, 45, 0]))!,
	decodeFrame(new Uint8Array([1, 0x20, 0x08, 0, 90]))!,
	decodeFrame(new Uint8Array([2, 0x40, 0x20, 166, 211]))!,
	decodeFrame(new Uint8Array([3, 0x10, 0x10, 0, 0]))!
];
const meta = {
	title: 'N64/Controller dashboard',
	component: ControllerDashboard,
	tags: ['autodocs'],
	args: {
		controllers,
		received: [true, true, true, true],
		connected: true,
		connection: 'connected',
		persistSettings: false
	}
} satisfies Meta<typeof ControllerDashboard>;
export default meta;
type Story = StoryObj<typeof meta>;
export const FourControllers: Story = {};
export const NarrowOBS: Story = { globals: { viewport: { value: 'obs', isRotated: false } } };
export const OnlyController3: Story = { args: { initialVisible: [2] } };
export const Controllers1And4: Story = { args: { initialVisible: [0, 3] } };
export const WaitingForInput: Story = {
	args: {
		controllers: Array.from({ length: 4 }, emptyState),
		received: [false, false, false, false]
	}
};
export const Disconnected: Story = {
	args: { connected: false, connection: 'disconnected (1006) — retrying…' }
};
export const NoControllers: Story = { args: { initialVisible: [] } };
export const VisibilitySettings: Story = {
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		await userEvent.click(canvas.getByText('Settings'));
		await userEvent.click(canvas.getByRole('button', { name: 'Only 1' }));
		await expect(canvas.getAllByRole('article')).toHaveLength(1);
		await userEvent.click(canvas.getByRole('checkbox', { name: '3' }));
		await expect(canvas.getAllByRole('article')).toHaveLength(2);
		await userEvent.click(canvas.getByRole('button', { name: 'Show all' }));
		await expect(canvas.getAllByRole('article')).toHaveLength(4);
	}
};

export const Minimal: Story = { args: { initialMinimal: true } };
export const MinimalOBS: Story = {
	args: { initialMinimal: true },
	globals: { viewport: { value: 'obs', isRotated: false } }
};
export const MinimalEmpty: Story = { args: { initialMinimal: true, initialVisible: [] } };
export const MinimalToggle: Story = {
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		await userEvent.click(canvas.getByText('Settings'));
		await userEvent.click(canvas.getByRole('checkbox', { name: 'Minimal interface' }));
		await expect(canvas.queryByRole('heading', { name: 'N64 SPY' })).toBeNull();
		await expect(canvas.getAllByRole('article')).toHaveLength(4);
		const exit = canvas.getByRole('button', { name: 'Exit minimal mode' });
		await expect(exit).toHaveFocus();
		await userEvent.click(exit);
		await expect(canvas.getByRole('heading', { name: 'N64 SPY' })).toBeVisible();
		await userEvent.click(canvas.getByRole('checkbox', { name: 'Minimal interface' }));
		await userEvent.keyboard('{Escape}');
		await expect(canvas.getByRole('heading', { name: 'N64 SPY' })).toBeVisible();
	}
};

export const ChromaGreen: Story = {
	args: { initialMinimal: true, initialBackground: '#00ff00' },
	globals: { viewport: { value: 'obs', isRotated: false } }
};
export const Transparent: Story = {
	args: { initialMinimal: true, initialBackground: 'transparent' }
};
export const BackgroundSettings: Story = {
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		await userEvent.click(canvas.getByText('Settings'));
		const input = canvas.getByRole('textbox', { name: 'Background color (CSS)' });
		await userEvent.clear(input);
		await userEvent.type(input, '#00ff00');
		await expect(input).toHaveAttribute('aria-invalid', 'false');
		await expect(canvasElement.querySelector('.surface')).toHaveStyle({
			backgroundColor: '#00ff00'
		});
		await userEvent.clear(input);
		await userEvent.type(input, 'not-a-color');
		await expect(input).toHaveAttribute('aria-invalid', 'true');
		await expect(canvasElement.querySelector('.surface')).toHaveStyle({
			backgroundColor: '#00ff00'
		});
		await userEvent.clear(input);
		await userEvent.type(input, 'transparent');
		await expect(canvasElement.querySelector('.surface')).toHaveStyle({
			backgroundColor: 'rgba(0, 0, 0, 0)'
		});
		await userEvent.click(canvas.getByRole('button', { name: 'Reset' }));
		await expect(input).toHaveValue('#101720');
	}
};
