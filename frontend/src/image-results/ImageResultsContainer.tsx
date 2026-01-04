import {Carousel} from "@mantine/carousel";

import type {ImageMatchResult, ImageSearchResults} from "../models/ImageSearchResults.ts";
import * as React from "react";
import {Image} from "@mantine/core";

import '@mantine/core/styles.css';
import '@mantine/carousel/styles.css';
import styles from './ImageResultsContainer.module.css'

const ImageResultsContainer: React.FC<ImageSearchResults> = ({ results }) => {
    return (
        <div style={{ height: 400, display: 'flex' }}>
        <Carousel
            // height={600}
            classNames={styles}
            height="100%" flex={1}
            slideSize={{ base: '100%', sm: '50%', md: '33.333333%' }}
            slideGap={{ base: 0, sm: 'md' }}
            controlsOffset="xs"
            controlSize={15}
            withControls={true}
            withIndicators={false}
            emblaOptions={{ loop: true, align: 'start', slidesToScroll: 3 }}
        >
            {results.map((result: ImageMatchResult) => (
                    <Carousel.Slide>
                        <Image
                            maw={"200px"}
                            mah={"200px"}
                            radius='md'
                            src={"data:image/jpeg;base64," + result.thumbnail}
                            alt={result.description}
                        />
                        <div>{result.description}</div>
                    </Carousel.Slide>
                ))
            }
        </Carousel>
        </div>
    );
}

export default ImageResultsContainer;