import type {ImageMatchResult, ImageSearchResults} from "../models/ImageSearchResults.ts";
import * as React from "react";
import {Grid, Image} from "@mantine/core";

import '@mantine/core/styles.css';
import '@mantine/carousel/styles.css';

const ImageResultsContainer: React.FC<ImageSearchResults> = ({ results }) => {
    return (
        <Grid
            miw={"80%"}
            align={"center"}
        >
            { results.map((result: ImageMatchResult) => (
                    <Grid.Col
                        span={3}
                    >
                        <Image
                            width={"256px"}
                            height={"256px"}
                            radius='md'
                            src={result.thumbnail}
                            alt={result.description}
                        />
                    </Grid.Col>
                ))
            }
        </Grid>
    );
}

export default ImageResultsContainer;