import ImageMatchSearch from "./image-match/ImageMatchSearch.tsx";
import {Box} from "@mantine/core";
import type ImageSearchContainerProps from "./ImageSearchContainerProps.ts";

const ImageSearchContainer: React.FC<ImageSearchContainerProps> = ({setSearchResults}: ImageSearchContainerProps) => {

    return (
        <Box pos="relative" maw={600} mx="auto" mt="xs">
            <ImageMatchSearch setSearchResults={setSearchResults}/>
        </Box>
    );
}

export default ImageSearchContainer;