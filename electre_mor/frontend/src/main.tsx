import { createRoot } from 'react-dom/client';

import App from './App';
import './styles/theme.css';

const container = document.getElementById('root');

if (!container) {
  throw new Error('Nao foi possivel localizar o elemento root.');
}

createRoot(container).render(<App />);
