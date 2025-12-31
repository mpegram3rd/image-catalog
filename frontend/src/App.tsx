import '@mantine/core/styles.css';

import './App.css'
import { MantineProvider } from "@mantine/core";
import ImageSearchContainer from "./image-search/ImageSearchContainer.tsx";

function App() {

  return (
    <MantineProvider >
        <ImageSearchContainer />
    </MantineProvider>
  )
}

export default App
