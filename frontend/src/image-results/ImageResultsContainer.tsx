import type {ImageMatchResult, ImageSearchResults} from "../models/ImageSearchResults.ts";
import * as React from "react";
import {Image, SimpleGrid} from "@mantine/core";

import '@mantine/core/styles.css';

const ImageResultsContainer: React.FC<ImageSearchResults> = ({ results }) => {
    return (
        <SimpleGrid cols={4} >
            { results.map((result: ImageMatchResult) => (
                    <div>
                        <Image
                            width={"256px"}
                            height={"256px"}
                            maw={"256px"}
                            mah={"256px"}
                            radius='md'
                            src={result.thumbnail}
                            alt={result.description}
                        />
                    </div>
                ))
            }
        </SimpleGrid>
    );
}

export default ImageResultsContainer;