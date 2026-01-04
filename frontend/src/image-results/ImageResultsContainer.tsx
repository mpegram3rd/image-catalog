import {Carousel} from "@mantine/carousel";

import '@mantine/core/styles.css';
import '@mantine/carousel/styles.css';
import styles from './ImageResultsContainer.module.css'
import type {ImageMatchResult, ImageSearchResults} from "../models/ImageSearchResults.ts";
import * as React from "react";

const ImageResultsContainer: React.FC<ImageSearchResults> = ({ results }) => {
    return (
        <Carousel
            height={200}
            className={styles.container}
            withIndicators={true}
            emblaOptions={{
                align: 'center'
            }}
        >
            {results.map((result: ImageMatchResult) => (
                    <Carousel.Slide>
                        <div><b>Image:</b> {result.image_path}</div>
                        <div><b>Description:</b> {result.description}</div>
                    </Carousel.Slide>
                ))
            }
        </Carousel>
    );
}

export default ImageResultsContainer;