import type {ImageDisplayProps} from "../models/ImageDisplayProps.ts";
import {Image, Modal, ScrollArea, Text} from "@mantine/core";

const ImageModal: React.FC<ImageDisplayProps> = ({isOpen, imagePath, description, onClose}) => {

    if (!imagePath) return null; // Don't render if no image data

    return (
        <Modal
            opened={isOpen}
            onClose={onClose}
            withCloseButton={false}
            centered
            size="md"
            styles={{
                header: { background: '#ddd' },
                content: { background: '#ddd' }
            }}
        >
            <Image
                src={imagePath}
                alt={description || "No description available"}
                radius="md"
                styles={{
                    root: { boxShadow: '0px 0px 15px rgba(0, 0, 0, 0.3)' }
                }}
            />
            <ScrollArea
                type="auto"
                h={150}
                offsetScrollbars
                styles={{
                    root: { marginTop: '10px' },
                    scrollbar: { background: 'inherit'}
                }}
            >
                <Text>{description || "No description available"}</Text>
            </ScrollArea>
        </Modal>
    )
}

export default ImageModal;