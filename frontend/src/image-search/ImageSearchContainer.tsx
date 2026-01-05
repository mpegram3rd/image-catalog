import ImageMatchSearch from "./image-match/ImageMatchSearch.tsx";
import {Box, LoadingOverlay} from "@mantine/core";
import type ImageSearchContainerProps from "./ImageSearchContainerProps.ts";
import {useState} from "react";

const ImageSearchContainer: React.FC<ImageSearchContainerProps> = ({setSearchResults}: ImageSearchContainerProps) => {

    const [isLoading, setLoading] = useState(false);

    return (

        <Box pos="relative" maw={600} mx="auto" mt="xs">
            <LoadingOverlay visible={isLoading} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />
            <ImageMatchSearch setSearchResults={setSearchResults} setLoading={setLoading} />
        </Box>
    );
}

export default ImageSearchContainer;