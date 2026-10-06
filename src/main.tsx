import {createRoot} from 'react-dom/client';
import {Workspace} from './Workspace';
import './style.css';
import './workspace.css';
const root=createRoot(document.getElementById('root')!);root.render(<Workspace/>);if(import.meta.hot)import.meta.hot.dispose(()=>root.unmount());
