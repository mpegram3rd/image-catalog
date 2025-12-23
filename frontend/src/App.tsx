import '@mantine/core/styles.css';

import './App.css'
import { MantineProvider } from "@mantine/core";
import ImageMatchContainer from "./image-match/ImageMatchContainer.tsx";

function App() {

  return (
    <MantineProvider>
        <ImageMatchContainer/>
    </MantineProvider>
  )
}

export default App
