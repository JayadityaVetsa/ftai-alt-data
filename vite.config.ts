import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],base:'/ftai-alt-data/',build:{chunkSizeWarningLimit:5000}});
