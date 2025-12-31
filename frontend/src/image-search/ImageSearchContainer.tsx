import TextSearchForm from "./text-search/TextSearchForm.tsx";
import ImageDropper from "./image-match/ImageDropper.tsx";
import {SimpleGrid} from "@mantine/core";

export default function ImageSearchContainer () {

    return (
        <SimpleGrid cols={2}>
            <TextSearchForm/>
            <ImageDropper/>
        </SimpleGrid>
    );
}