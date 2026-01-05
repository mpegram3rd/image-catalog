import {Dropzone, type FileRejection, MIME_TYPES} from '@mantine/dropzone';
import {IconPhoto, IconUpload, IconX} from '@tabler/icons-react';
import {Box, Group, rem, Text} from '@mantine/core';
import type {ImageMatchResult, ImageSearchResults} from "../../models/ImageSearchResults.ts";
import {useState} from "react";
import TextSearch from "../text-match/TextSearch.tsx";
import type ImageSearchContainerProps from "../ImageSearchContainerProps.ts";

// TODO move this over into a service
async function uploadFile(file: File): Promise<ImageSearchResults> {
    const formData = new FormData();
    formData.append('file', file);
    try {
        const result = await fetch("http://localhost:8000/api/search/image", {
            method: 'POST',
            body: formData
        });
        const data = (await result.json()) as ImageMatchResult[];

        return {
            results: data
        } as ImageSearchResults;
    }
    catch (error) {
        console.error(error);
    }
    return {
        results: []
    } as ImageSearchResults;
}

const ImageMatchSearch: React.FC<ImageSearchContainerProps> = ({setSearchResults, setLoading}: ImageSearchContainerProps) => {
    const [isHovering, setIsHovering] = useState(false);

    const handleFileDrop = async (files: File[]) => {
        setLoading(true);
        setIsHovering(false);
        console.log('Dropzone dropped file: ', files[0].name);
        await uploadFile(files[0])
            .then((searchResults   ) => {
                setSearchResults(searchResults);
            })
            .catch((error) => {
                console.error(error);
            });
        setLoading(false);
    }

    const handleRejectedFile = (fileRejections: FileRejection[]) => {
        setIsHovering(false);
        console.error(`File Upload failed: ${fileRejections[0].errors[0].message}`);
    }

    return (
        <Dropzone
            accept={[
                MIME_TYPES.png,
                MIME_TYPES.jpeg
            ]}
            maxSize={10 * 1024 ** 2}
            onDrop={handleFileDrop}
            onReject={handleRejectedFile}
            // We deactivate clicking so the Textarea remains interactive
            activateOnClick={false}
            onDragEnter={() => setIsHovering(true)}
            onDragLeave={() => setIsHovering(false)}
            styles={{
                root: {
                    border: isHovering ? undefined : 'none',
                    padding: 0,
                    backgroundColor: 'transparent',
                    transition: 'all 0.2s ease',
                },
            }}
        >
            {isHovering ? (
                <Box
                    style={{
                        height: rem(120),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: `${rem(2)} dashed var(--mantine-color-blue-6)`,
                        borderRadius: 'var(--mantine-radius-md)',
                        backgroundColor: 'var(--mantine-color-blue-light)',
                        pointerEvents: 'none',
                    }}
                    miw={600}
                >
                    <Group justify="center" gap="xl" style={{ pointerEvents: 'none' }}>
                        <Dropzone.Accept>
                            <IconUpload size="3.2rem" stroke={1.5} />
                        </Dropzone.Accept>
                        <Dropzone.Reject>
                            <IconX size="3.2rem" stroke={1.5} />
                        </Dropzone.Reject>
                        <Dropzone.Idle>
                            <IconPhoto size="3.2rem" stroke={1.5} />
                        </Dropzone.Idle>

                        <div>
                            <Text size="xl" inline>
                                Drop Images here to search
                            </Text>
                            <Text size="sm" c="dimmed" inline mt={7}>
                                Release to attach to your message
                            </Text>
                        </div>
                    </Group>
                </Box>
            ) : (
                <TextSearch setSearchResults={setSearchResults} setLoading={setLoading}/>
            )}
        </Dropzone>

    );
}

export default ImageMatchSearch;