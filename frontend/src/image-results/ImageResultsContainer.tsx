import type {ImageMatchResult, ImageSearchResults} from "../models/ImageSearchResults.ts";
import * as React from "react";
import {useState} from "react";
import {Image, SimpleGrid} from "@mantine/core";

import '@mantine/core/styles.css';
import ImageModal from "./ImageModal.tsx";

const ImageResultsContainer: React.FC<ImageSearchResults> = ({ results }) => {

    const [modalOpen, setModalOpen] = useState(false);
    const [imagePath, setImagePath] = useState<string | undefined>(undefined);
    const [description, setDescription] = useState<string | undefined>(undefined);

    const handleOpenModal = (imagePath: string, description: string) => {
        setModalOpen(true);
        setImagePath(imagePath);
        setDescription(description);
    }

    const handleCloseModal = () => {
        setModalOpen(false);
        setImagePath(undefined);
        setDescription(undefined);
    }

    return (
        <>
            <SimpleGrid cols={4} >
                { results.map((result: ImageMatchResult) => (
                        <div key={result.image_path}>
                            <Image
                                width={"256px"}
                                height={"256px"}
                                maw={"256px"}
                                mah={"256px"}
                                radius='md'
                                src={result.thumbnail}
                                alt={result.description}
                                onClick={() => {
                                    handleOpenModal(result.image_path, result.description);

                                }}
                            />
                        </div>
                    ))
                }
            </SimpleGrid>
            <ImageModal
                isOpen={modalOpen}
                imagePath={imagePath}
                description={description}
                onClose={handleCloseModal}
            />

        </>
    );
}

export default ImageResultsContainer;