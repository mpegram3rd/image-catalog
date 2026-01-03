import ImageMatchSearch from "./image-match/ImageMatchSearch.tsx";
import {Box} from "@mantine/core";

export default function ImageSearchContainer () {

    return (
        <Box pos="relative" maw={600} mx="auto" mt="xl">
            <ImageMatchSearch/>
        </Box>
    );
}