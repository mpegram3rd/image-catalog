import {Carousel} from "@mantine/carousel";

import type {ImageMatchResult, ImageSearchResults} from "../models/ImageSearchResults.ts";
import * as React from "react";
import {Image} from "@mantine/core";

import '@mantine/core/styles.css';
import '@mantine/carousel/styles.css';
import styles from './ImageResultsContainer.module.css'

const ImageResultsContainer: React.FC<ImageSearchResults> = ({ results }) => {
    return (
        <Carousel
            height={200}
            className={styles.container}
            withIndicators={true}
            slideSize={"80%"}
            classNames={{slide: styles.slides}}
            emblaOptions={{
                loop: true,
                dragFree: false,
                align: 'center'
            }}
        >
            {results.map((result: ImageMatchResult) => (
                    <Carousel.Slide>
                        <Image
                            radius='md'
                            src={result.image_path}
                        />
                        <div>{result.description}</div>
                    </Carousel.Slide>
                ))
            }
        </Carousel>
    );
}

export default ImageResultsContainer;