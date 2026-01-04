import '@mantine/core/styles.css';

import './App.css'
import { MantineProvider } from "@mantine/core";
import ImageSearchContainer from "./image-search/ImageSearchContainer.tsx";
import ImageResultsContainer from "./image-results/ImageResultsContainer.tsx";
import {useState} from "react";
import type {ImageSearchResults} from "./models/ImageSearchResults.ts";

export default function App() {

    const [searchResults, setSearchResults] = useState<ImageSearchResults>({ results: [] });

    return (
        <MantineProvider >
            <ImageSearchContainer setSearchResults={setSearchResults} />
            <ImageResultsContainer results={searchResults.results} />
        </MantineProvider>
    )
}
