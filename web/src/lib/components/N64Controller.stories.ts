import type { Meta, StoryObj } from '@storybook/sveltekit';
import N64Controller from './N64Controller.svelte';
import { decodeFrame, emptyState } from '../controller';
const meta = {
	title: 'N64/Controller',
	component: N64Controller,
	tags: ['autodocs'],
	args: { controller: emptyState(), number: 1 },
	parameters: { layout: 'padded' }
} satisfies Meta<typeof N64Controller>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Idle: Story = {};
export const EveryButtonPressed: Story = {
	args: { controller: decodeFrame(new Uint8Array([0, 255, 63, 0, 0]))! }
};
export const StickTopRight: Story = {
	args: { controller: decodeFrame(new Uint8Array([0, 0, 0, 90, 90]))! }
};
export const StickBottomLeft: Story = {
	args: { controller: decodeFrame(new Uint8Array([0, 0, 0, 128, 128]))! }
};
