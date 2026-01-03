import {Carousel} from "@mantine/carousel";

import '@mantine/core/styles.css';
import '@mantine/carousel/styles.css';
import styles from './ImageResultsContainer.module.css'

export default function ImageResultsContainer () {
    return (
        <Carousel
            height={200}
            className={styles.container}
            withIndicators={true}
            emblaOptions={{
                align: 'center'
            }}
        >
            <Carousel.Slide>1</Carousel.Slide>
            <Carousel.Slide>2</Carousel.Slide>
            <Carousel.Slide>3</Carousel.Slide>
        </Carousel>
    );
}