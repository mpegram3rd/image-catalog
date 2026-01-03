import '@mantine/core/styles.css';

import './App.css'
import { MantineProvider } from "@mantine/core";
import ImageSearchContainer from "./image-search/ImageSearchContainer.tsx";
import ImageResultsContainer from "./image-results/ImageResultsContainer.tsx";

function App() {

  return (
    <MantineProvider >
        <ImageSearchContainer />
        <ImageResultsContainer/>
    </MantineProvider>
  )
}

export default App
