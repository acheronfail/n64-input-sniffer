import type { Meta, StoryObj } from '@storybook/sveltekit';
import LiveDemo from './LiveDemo.svelte';
const meta = { title: 'N64/Live demo', component: LiveDemo } satisfies Meta<typeof LiveDemo>;
export default meta;
type Story = StoryObj<typeof meta>;
export const FourMovingControllers: Story = {};
export const OBS: Story = { globals: { viewport: { value: 'obs', isRotated: false } } };
